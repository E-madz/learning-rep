-- Dev only: Django's test runner must be able to CREATE the test_cloudlab database.
GRANT ALL PRIVILEGES ON *.* TO 'cloudlab'@'%';
FLUSH PRIVILEGES;
