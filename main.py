if __name__ == "__main__":
    from handler import dispatcher, executor, notify_admins_start, notify_admins_end
    executor.start_polling(dispatcher, on_startup=notify_admins_start, on_shutdown=notify_admins_end)
