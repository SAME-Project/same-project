from setuptools import setup


setup(name='same_kernel',
      version='0.0.1',
      description='A Python kernel for running on SAME backend.',
      long_description='A Python kernel for Jupyter/IPython to run on SAME backend, based on MetaKernel',
      author='Gohar Irfan Chaudhry',
      author_email='gohar.irfan@microsoft.com',
      install_requires=['metakernel', 'jedi'],
      py_modules=['same_kernel'],
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)
