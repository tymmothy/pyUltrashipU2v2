from distutils.core import setup
setup(name='ultraship_u2v2',
      version='0.1',
      author='Tymm Twillman',
      author_email='tymmothy@gmail.com',
      description='Ultraship U2 Scale (version 2 / USB serial interface) module',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
      ],
      license='BSD-new',
      requires=[
          'pySerial',
      ],
      provides=[
          'ultraship_u2v2',
      ],
      py_modules=['ultraship_u2v2'],
      )

