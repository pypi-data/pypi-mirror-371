from setuptools import setup, find_packages

setup(
    name="service-sms",  # nom du package
    version="0.1.0",
    description="Un package Python pour envoyer des SMS via Airtel et des messages WhatsApp (OTP).",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Abdou Khamiss",
    author_email="abdougarbahamissou833@gmail.com",
    url="https://github.com/ton-compte/service-sms",
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
