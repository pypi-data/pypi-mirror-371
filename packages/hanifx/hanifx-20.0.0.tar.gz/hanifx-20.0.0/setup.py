from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hanifx",
    version="20.0.0",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="Offline OTP Generator (TOTP/HOTP) with QR and backup codes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-540",  # Update your repo URL
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=["qrcode[pil]"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
