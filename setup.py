from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='cce-netlab-umb',
    version="0.0.1",
    author="Xiaoqian Zhang",
    author_email="haoyuumb@gmail.com",
    description="A small utils package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TiffanyXQZ/cce-scripts",
    project_urls={
        "Bug Tracker": "https://github.com/TiffanyXQZ/cce-scripts/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    extras_require=dict(tests=['pytest']),
    entry_points = {
        'console_scripts':[
            'cce=cce.autorun:app'
        ]
    }
)
