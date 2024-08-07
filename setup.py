"""Setup for skyroom XBlock."""


import os

from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name="skyroom-xblock",
    author="edSPIRIT",
    description="a simple XBlock to login users to SkyRoom",
    version="0.2.2",
    license="MIT",
    packages=[
        "skyroom",
    ],
    install_requires=[
        "xblock",
        "requests==2.31.0",
    ],
    entry_points={
        "xblock.v1": [
            "skyroom = skyroom:SkyRoomXBlock",
        ]
    },
    package_data=package_data(
        "skyroom", ["static", "public", "locale", "translations"]
    ),
)
