FROM prefecthq/prefect:2.8-python3.9

# Install dependencies
COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt --no-cache-dir --trusted-host pypi.python.org

# Copy the rest of the code

COPY . /opt/prefect/flows

# install pt_BR locale
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* && localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8

# Set the locale
#ENV LANG=en_US.UTF-8 \
#    LANGUAGE=en_US:en \
#    LC_ALL=en_US.UTF-8
ENV LANG=pt_BR.UTF-8 \
    LANGUAGE=pt_BR:pt \
    LC_ALL=pt_BR.UTF-8

# Set the timezone
ENV TZ America/Sao_Paulo

# Set the working directory
WORKDIR /opt/prefect/flows
