from setuptools import setup, find_packages

setup(name='pyECG_graph',
      packages=find_packages(),
      version='0.1',
      description='Python utility to generate ECG (Electrocardiogram) graph',
      url='https://github.com/KartikeyaRokde/pyECG_graph',
      author='Kartikeya Rokde',
      author_email='kartik.a.rokde@gmail.com',
      license='MIT',
      package_data={'': ['*.svg', '*.js']},
      zip_safe=False)
