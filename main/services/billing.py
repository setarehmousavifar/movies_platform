"""Billing / entitlement domain services (future app: billing)."""

from datetime import date, timedelta

from django.db import transaction

from main.exceptions import PermissionDeniedError, ValidationDomainError
from main.models import AuditLog, Subscription
from main.permissions import is_premium_user, is_staff_user


class AuditService:
    @staticmethod
    def log(*, actor, action: str, target_type: str = '', target_id: str = '', metadata: dict | None = None):
        AuditLog.objects.create(
            actor=actor if getattr(actor, 'is_authenticated', False) else None,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else '',
            metadata=metadata or {},
        )


class EntitlementService:
    """Access rules for premium-gated resources (downloads, etc.)."""

    @staticmethod
    def can_download(user) -> bool:
        return is_premium_user(user)

    @staticmethod
    def assert_can_download(user):
        if not EntitlementService.can_download(user):
            raise PermissionDeniedError('Premium subscription required to download.')


class SubscriptionService:
    @staticmethod
    def current_for(user):
        return (
            Subscription.objects.filter(user=user).order_by('-end_date', '-id').first()
        )

    @staticmethod
    @transaction.atomic
    def assign(
        *,
        user,
        actor,
        subscription_type: str,
        end_date: date,
        start_date: date | None = None,
        reason: str = 'staff_assign',
    ) -> Subscription:
        """Only staff may grant/change premium. Basic can be assigned by staff too."""
        if not is_staff_user(actor):
            raise PermissionDeniedError('Only staff can assign subscriptions.')
        if subscription_type not in ('basic', 'premium'):
            raise ValidationDomainError('Invalid subscription type.')
        start = start_date or date.today()
        if end_date < start:
            raise ValidationDomainError('end_date must be on or after start_date.')

        # Deactivate previous active rows for clarity
        Subscription.objects.filter(user=user, is_active=True).update(is_active=False)

        sub = Subscription.objects.create(
            user=user,
            subscription_type=subscription_type,
            start_date=start,
            end_date=end_date,
            is_active=True,
        )
        user.sync_premium_flag()
        AuditService.log(
            actor=actor,
            action='subscription.assign',
            target_type='user',
            target_id=user.pk,
            metadata={
                'subscription_id': sub.pk,
                'subscription_type': subscription_type,
                'start_date': str(start),
                'end_date': str(end_date),
                'reason': reason,
            },
        )
        return sub

    @staticmethod
    @transaction.atomic
    def request_upgrade(*, user, note: str = '') -> None:
        """Users may request premium; staff must approve via admin/assign."""
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        AuditService.log(
            actor=user,
            action='subscription.upgrade_requested',
            target_type='user',
            target_id=user.pk,
            metadata={'note': note[:500]},
        )

    @staticmethod
    @transaction.atomic
    def grant_demo_premium_days(*, user, actor, days: int = 30) -> Subscription:
        """Controlled demo path: staff-only mock checkout for thesis demos."""
        if not is_staff_user(actor):
            raise PermissionDeniedError('Only staff can run mock checkout.')
        return SubscriptionService.assign(
            user=user,
            actor=actor,
            subscription_type='premium',
            end_date=date.today() + timedelta(days=days),
            reason='mock_checkout',
        )
