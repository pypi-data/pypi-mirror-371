from setuptools import setup, find_packages

setup(
    name="jwt_pro",
    version="1.0.2",
    author="krishna Tadi",
    description="JWT Pro is your all-in-one tool for working with JSON Web Tokens (JWTs) in Python. Whether you need to generate, verify, decode, or inspect tokens, JWT Pro makes it simple, safe, and developer-friendly.  ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/krishnatadi/jwt-pro-python",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "jwt-pro=jwt_pro.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "alluuid==0.1.0",
        "cryptography==38.0.0"
    ],
    keywords='"JWT", "JWT PRO", "JWT-PRO", "authentication", "security", "token", "AES", "encryption", "HMAC", "JWT verification", "Python security", "cryptography", "secure tokens", "token verification", "token generation"',
    project_urls={
    'Documentation': 'https://github.com/krishnatadi/jwt-pro-python#readme',
    'Source': 'https://github.com/krishnatadi/jwt-pro-python',
    'Issue Tracker': 'https://github.com/krishnatadi/jwt-pro-python/issues',
    },
    license='MIT'
)
