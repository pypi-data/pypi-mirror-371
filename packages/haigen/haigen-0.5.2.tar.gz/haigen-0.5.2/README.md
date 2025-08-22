Laborit Haigen

Como fazer o upload de uma nova versão?

- 1 Primeiro passo é atualizar/instalar o pip. Lembrando de ter o python 3.11+ instalado.
$ python -m pip install --upgrade pip

- 2 Instalar as libs setuptools, wheel e twine
$ pip install setuptools wheel twine 

- 3 É necessário atualizar o arquivo 'setup.py' com a versão nova
''' 
setup(
    name='luis_laborit_teste',
    version='x.x',# <-- Versão nova aqui
    packages=find_packages(),
    install_requires=[
        
    ]
)
'''

- 4 Excluir pastas antigas de build/distribuição 
$ rm -Rf /build
$ rm -Rf /dist
$ rm -Rf /heigen.egg-info


- 5 Criar o build do pacote e criar a pasta /dist para distribuição
$ python setup.py sdist bdist_wheel

- 6 fazer o upload do pacote para o PyPi
$ twine upload dist/*

*Obs, você precisará fornecer o token do PyPi nesse passo. Quando você subir, ele localizará
o repositório PyPi através do nome do pacote, versão e tipo de distribuição. O PyPi irá
ver através do seu token se você tem acesso de owner ou mantainer do projeto para permitir
a subida.