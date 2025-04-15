from setuptools import setup

setup(
    name="telegram-bot",
    version="0.1",
    python_requires=">=3.11,<3.12",
    install_requires=[
        "python-telegram-bot>=20.3",
        "huggingface-hub>=0.19.4",
        "python-dotenv>=1.0.0",
        "transformers>=4.36.2",
        "accelerate>=0.25.0"
    ],
)