# from app import create_app
# from utils.scheduler_utils import setup_scheduler, shutdown_scheduler

# app = create_app()  # Initialize the app

# # Set up the scheduler
# scheduler = setup_scheduler()

# # Handle graceful shutdown
# shutdown_scheduler(scheduler)

# if __name__ == '__main__':
#     try:
#         app.run(host='0.0.0.0', port=5000, debug=True)
#     except (KeyboardInterrupt, SystemExit):
#         scheduler.shutdown()
