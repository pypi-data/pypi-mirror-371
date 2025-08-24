from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alert-after-pro",
    version="0.2.2",
    author="Alert After Pro Team",
    author_email="alert@afterpro.dev",
    description="Get notified when your commands complete - supports Telegram, SMS, DingDing, Ntfy, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MatrixA/alert-after-pro",
    project_urls={
        "Bug Reports": "https://github.com/MatrixA/alert-after-pro/issues",
        "Source": "https://github.com/MatrixA/alert-after-pro",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
    ],
    extras_require={
        "sms": ["twilio>=7.0.0"],
        "all": ["twilio>=7.0.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "aa=alert_after_pro.main:main",
        ],
    },
    keywords="notification alert command monitoring telegram sms dingding ntfy",
    include_package_data=True,
    zip_safe=False,
)