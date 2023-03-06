FROM prefecthq/prefect:2-python3.9

# Install the agent
RUN pip install prefect[agent]

# run the agent
CMD ["prefect", "agent", "docker", "start"]