FROM prefecthq/prefect:2.8-python3.9

# Install dependencies
COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt --no-cache-dir --trusted-host pypi.python.org

# Copy the rest of the code

COPY . /opt/prefect/flows

# install pt_BR locale
RUN sudo apt-get update && sudo apt-get install -y locales && sudo locale-gen pt_BR.UTF-8
