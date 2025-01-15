import logging

class TokenDispenserLogger:
    _instances = {}

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.logger = logging.getLogger(f"TokenDispenserLogger_{client_id}")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(f'%(asctime)s - %(levelname)s -client_id: {client_id} : %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    @classmethod
    def get_instance(cls, client_id: str):
        if client_id not in cls._instances:
            cls._instances[client_id] = cls(client_id)
        return cls._instances[client_id]

    @classmethod
    def get_logger(cls):
        if not cls._instances:
            raise ValueError(
                "No TokenDispenserLogger instance has been initialized. Call get_instance(client_id) first.")
        # Return the first logger instance
        return next(iter(cls._instances.values())).logger

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warn(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)