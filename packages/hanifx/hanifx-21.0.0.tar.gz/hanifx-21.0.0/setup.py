from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hanifx",
    version="21.0.0",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="Professional OTP module with backup codes and QR generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-540",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "qrcode[pil]"
    ],
)
