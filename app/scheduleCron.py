from crontab import CronTab



my_cron = CronTab(user = 'parallax')
for job in my_cron:
    print(job)

job = my_cron.new(command='/usr/bin/python3 /home/parallax/algo_trading/app/jobs_scheduler.py >> ~/cron.log 2>&1')
# job.minute.every(1)
my_cron.write()




# 1 * * * * /usr/bin/python3 /home/parallax/algo_trading/app/writeDate.py >> ~/cron.log 2>&1
