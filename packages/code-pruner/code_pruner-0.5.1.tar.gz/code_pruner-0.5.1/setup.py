from setuptools import setup


def readme():
    with open('ReadMe.md') as f:
        return f.read()
    
def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name='code_pruner',
    version='0.5.1',
    packages=['code_pruner'],
    url='',
    license='MIT License',
    author='liubomyr.ivanitskyi',
    author_email='lubomyr.ivanitskiy@gmail.com',
    description='A tool to prune Python code based on specified patterns.',
    long_description=readme(),
    install_requires=read_requirements(),
    long_description_content_type="text/markdown"
)