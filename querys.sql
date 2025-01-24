use movieplatform

DESCRIBE users;

SELECT * FROM Users;

-- پربازدیدترین فیلم‌ها
SELECT Title, View_Count
FROM Movies
ORDER BY View_Count DESC
LIMIT 5;

-- فیلم‌های یک ژانر خاص
SELECT Movies.Title, Genres.Genre_Name
FROM Movies
JOIN Movie_Genre ON Movies.ID = Movie_Genre.Movie_ID
JOIN Genres ON Movie_Genre.Genre_ID = Genres.ID
WHERE Genres.Genre_Name = 'Sci-Fi';

-- امتیازدهی کاربران
SELECT Users.Name, Movies.Title, Reviews.Rating, Reviews.Review_Text
FROM Reviews
JOIN Users ON Reviews.User_ID = Users.ID
JOIN Movies ON Reviews.Movie_ID = Movies.ID
ORDER BY Reviews.Rating DESC;

-- کاربران فعال (بر اساس تاریخچه تماشا)
SELECT Users.Name, COUNT(Watch_History.Movie_ID) AS Movies_Watched
FROM Watch_History
JOIN Users ON Watch_History.User_ID = Users.ID
GROUP BY Users.ID, Users.Name
ORDER BY Movies_Watched DESC;

-- تحلیل اشتراک‌ها
SELECT Subscription_Type, COUNT(*) AS Total_Users
FROM Subscriptions
GROUP BY Subscription_Type;

-- فیلم‌های محبوب (بر اساس امتیاز)
SELECT Movies.Title, AVG(Reviews.Rating) AS Average_Rating
FROM Reviews
JOIN Movies ON Reviews.Movie_ID = Movies.ID
GROUP BY Movies.ID, Movies.Title
ORDER BY Average_Rating DESC
LIMIT 5;

-- تراکنش‌های مالی کیف پول
SELECT Users.Name, Wallet_Transactions.Transaction_Type, Wallet_Transactions.Amount, Wallet_Transactions.Transaction_Date
FROM Wallet_Transactions
JOIN Users ON Wallet_Transactions.User_ID = Users.ID
ORDER BY Wallet_Transactions.Transaction_Date DESC;

-- فیلم‌های پیشنهادی بر اساس ژانر محبوب کاربر
SELECT Movies.Title, Genres.Genre_Name
FROM Movies
JOIN Movie_Genre ON Movies.ID = Movie_Genre.Movie_ID
JOIN Genres ON Movie_Genre.Genre_ID = Genres.ID
JOIN User_Genre_Preference ON Genres.ID = User_Genre_Preference.Genre_ID
WHERE User_Genre_Preference.User_ID = 1;

-- کاربران با بیشترین هزینه کیف پول
SELECT Users.Name, SUM(Wallet_Transactions.Amount) AS Total_Spent
FROM Wallet_Transactions
JOIN Users ON Wallet_Transactions.User_ID = Users.ID
WHERE Wallet_Transactions.Transaction_Type = 'Withdrawal'
GROUP BY Users.ID, Users.Name
ORDER BY Total_Spent DESC;

-- تحلیل ژانرهای محبوب
SELECT Genres.Genre_Name, COUNT(Movie_Genre.Movie_ID) AS Total_Movies
FROM Genres
JOIN Movie_Genre ON Genres.ID = Movie_Genre.Genre_ID
GROUP BY Genres.ID, Genres.Genre_Name
ORDER BY Total_Movies DESC;

--  تحلیل کاربران بدون اشتراک فعال
SELECT Users.Name, Users.Email
FROM Users
LEFT JOIN Subscriptions ON Users.ID = Subscriptions.User_ID
WHERE Subscriptions.ID IS NULL OR Subscriptions.End_Date < CURDATE();

-- شناسایی فیلم‌هایی که بیشترین نقد را دارند
SELECT Movies.Title, COUNT(Reviews.ID) AS Total_Reviews
FROM Movies
JOIN Reviews ON Movies.ID = Reviews.Movie_ID
GROUP BY Movies.ID, Movies.Title
ORDER BY Total_Reviews DESC
LIMIT 5;

-- کاربران با فعالیت بالا (نقد + تماشا)
SELECT Users.Name,
       (SELECT COUNT(*) FROM Reviews WHERE Reviews.User_ID = Users.ID) AS Total_Reviews,
       (SELECT COUNT(*) FROM Watch_History WHERE Watch_History.User_ID = Users.ID) AS Total_Watched,
       (SELECT COUNT(*) FROM Watch_History WHERE Watch_History.User_ID = Users.ID) +
       (SELECT COUNT(*) FROM Reviews WHERE Reviews.User_ID = Users.ID) AS Total_Activity
FROM Users
ORDER BY Total_Activity DESC;

-- شناسایی کاربران نزدیک به پایان اشتراک
SELECT Users.Name, Users.Email, Subscriptions.End_Date
FROM Subscriptions
JOIN Users ON Subscriptions.User_ID = Users.ID
WHERE Subscriptions.End_Date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY);

-- تحلیل کیفیت و لینک دانلود
SELECT Movies.Title, Video_Quality.Quality, Video_Quality.Stream_URL, Download_Links.Link_URL
FROM Movies
LEFT JOIN Video_Quality ON Movies.ID = Video_Quality.Movie_ID
LEFT JOIN Download_Links ON Movies.ID = Download_Links.Movie_ID
ORDER BY Movies.Title;

-- محاسبه میانگین امتیازات برای ژانرهای خاص
SELECT Genres.Genre_Name, AVG(Reviews.Rating) AS Average_Rating
FROM Genres
JOIN Movie_Genre ON Genres.ID = Movie_Genre.Genre_ID
JOIN Reviews ON Movie_Genre.Movie_ID = Reviews.Movie_ID
GROUP BY Genres.ID, Genres.Genre_Name
ORDER BY Average_Rating DESC;

-- نمایش کارگردانان پربازدید
SELECT Directors.Name, COUNT(Movie_Directors.Movie_ID) AS Total_Movies, SUM(Movies.View_Count) AS Total_Views
FROM Directors
JOIN Movie_Directors ON Directors.ID = Movie_Directors.Director_ID
JOIN Movies ON Movie_Directors.Movie_ID = Movies.ID
GROUP BY Directors.ID, Directors.Name
ORDER BY Total_Views DESC;

-- نمایش سریال‌ها و تعداد فصل‌هایشان
SELECT Movies.Title AS Series_Title, COUNT(Seasons.ID) AS Total_Seasons
FROM Movies
JOIN Seasons ON Movies.ID = Seasons.Series_ID
WHERE Movies.Type = 'Series'
GROUP BY Movies.ID, Movies.Title;

--  نمایش فصل‌ها و تعداد قسمت‌هایشان
SELECT Seasons.Title AS Season_Title, COUNT(Episodes.ID) AS Total_Episodes
FROM Seasons
JOIN Episodes ON Seasons.ID = Episodes.Season_ID
GROUP BY Seasons.ID, Seasons.Title;

-- نمایش اطلاعات کامل قسمت‌های یک سریال خاص
SELECT Movies.Title AS Series_Title, Seasons.Season_Number, Episodes.Episode_Number, Episodes.Title AS Episode_Title, Episodes.Duration
FROM Movies
JOIN Seasons ON Movies.ID = Seasons.Series_ID
JOIN Episodes ON Seasons.ID = Episodes.Season_ID
WHERE Movies.Title = 'Breaking Bad'
ORDER BY Seasons.Season_Number, Episodes.Episode_Number;

-- نمایش فیلم‌های مورد علاقه کاربران
SELECT Users.Name AS User_Name, Movies.Title AS Favorite_Movie
FROM Favorite_Movies
JOIN Users ON Favorite_Movies.User_ID = Users.ID
JOIN Movies ON Favorite_Movies.Movie_ID = Movies.ID;

-- نمایش بازیگران و فیلم‌هایشان
SELECT Actors.Name AS Actor_Name, Movies.Title AS Movie_Title
FROM Movie_Actors
JOIN Actors ON Movie_Actors.Actor_ID = Actors.ID
JOIN Movies ON Movie_Actors.Movie_ID = Movies.ID;

-- نمایش بازیگران پربازدید
SELECT Actors.Name,
       COUNT(Movie_Actors.Movie_ID) AS Total_Movies,
       SUM(Movies.View_Count) AS Total_Views
FROM Actors
JOIN Movie_Actors ON Actors.ID = Movie_Actors.Actor_ID
JOIN Movies ON Movie_Actors.Movie_ID = Movies.ID
GROUP BY Actors.ID, Actors.Name
ORDER BY Total_Views DESC;

-- تست جامع پرس‌وجوها (Queries)
-- کوئری برای نمایش اطلاعات کامل فیلم‌ها و سریال‌ها
SELECT Movies.Title,
       Movies.Type,
       Movies.Release_Date,
       Movies.Description,
       Age_Ratings.Rating_Code AS Age_Rating,
       Age_Ratings.Description AS Rating_Description
FROM Movies
LEFT JOIN Age_Ratings ON Movies.Age_Rating_ID = Age_Ratings.ID;

-- فیلم‌ها و سریال‌های پرمخاطب بر اساس تعداد بازدید
SELECT Title, Type, View_Count
FROM Movies
ORDER BY View_Count DESC
LIMIT 5;

--  پیشنهاد محتوا به کاربر بر اساس ژانرهای مورد علاقه
SELECT Movies.Title, Genres.Genre_Name
FROM Movies
JOIN Movie_Genre ON Movies.ID = Movie_Genre.Movie_ID
JOIN Genres ON Movie_Genre.Genre_ID = Genres.ID
JOIN User_Genre_Preference ON Genres.ID = User_Genre_Preference.Genre_ID
WHERE User_Genre_Preference.User_ID = 1;

-- نمایش همه مدیران (Admins)
SELECT * FROM Users WHERE Role = 'Admin';

--  نمایش همه کاربران (Users)
SELECT * FROM Users WHERE Role = 'User';

-- نمایش کاربران فعال‌تر (آخرین ورود)
SELECT Name, Email, Last_Login
FROM Users
ORDER BY Last_Login DESC;

-- ب) شناسایی کاربران غیرفعال (بدون ورود)
SELECT Name, Email
FROM Users
WHERE Last_Login IS NULL;

-- نمایش تعداد کاربران فعال در بازه زمانی خاص
SELECT COUNT(*)
FROM Users
WHERE Last_Login >= DATE_SUB(NOW(), INTERVAL 7 DAY);

-- شناسایی کاربران غیرفعال برای بیش از 30 روز
SELECT Name, Email
FROM Users
WHERE Last_Login < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- محاسبه و نمایش میانگین امتیازات برای بررسی
SELECT Movies.ID, Movies.Title, AVG(Reviews.Rating) AS Average_Rating
FROM Movies
LEFT JOIN Reviews ON Movies.ID = Reviews.Movie_ID
GROUP BY Movies.ID, Movies.Title;

-- نمایش ساختار پاسخ‌ها
SELECT
    r1.ID AS Review_ID,
    r1.Review_Text AS Main_Review,
    r2.ID AS Response_ID,
    r2.Review_Text AS Response_Text
FROM Reviews r1
LEFT JOIN Reviews r2 ON r1.ID = r2.Parent_ID
WHERE r1.Movie_ID = 1
ORDER BY r1.ID, r2.ID;

-- الف) نمایش نقدهای بدون پاسخ
SELECT * FROM Reviews
WHERE Parent_ID IS NULL;

-- ب) نمایش تمام پاسخ‌های یک نقد خاص
SELECT * FROM Reviews
WHERE Parent_ID = 1; -- پاسخ به نقد شماره 1

-- ج) نمایش نقدها به همراه تعداد پاسخ‌ها
SELECT r1.ID AS Review_ID,
       r1.Review_Text AS Main_Review,
       COUNT(r2.ID) AS Total_Responses
FROM Reviews r1
LEFT JOIN Reviews r2 ON r1.ID = r2.Parent_ID
GROUP BY r1.ID, r1.Review_Text;

-- نمایش تگ های هر فیلم
SELECT Movies.Title, Tags.Tag_Name
FROM Movie_Tags
JOIN Movies ON Movie_Tags.Movie_ID = Movies.ID
JOIN Tags ON Movie_Tags.Tag_ID = Tags.ID;
