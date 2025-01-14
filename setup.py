from setuptools import setup

setup(
    name="regulatory_chatbot",
    version="1.0.0",
    packages=["regulatory_chatbot"],
    install_requires=[
        "pandas",
        "python-docx",
        "requests",
        "tkinter",
        "typing",
    ],
    entry_points={
        "console_scripts": [
            "regulatory_chatbot=regulatory_chatbot.chatbot_interface:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A regulatory compliance chatbot",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="regulatory compliance, chatbot, regulations",
    url="https://your-repository-url.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
) 