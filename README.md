# Akit-Bootstrap

Akit-Bootstrap is a tool to help you get started with the AgentKit platform. It will create a new project for you and set up the necessary files and directories to get you started.

## Installation

To install the akit-bootstrap tool, you can use pip:

```bash

pip install akit-bootstrap

```

## Usage

To create a new project, you can use the following command:

```bash
akit init 
```

Akit will automatically query you if there is missing information. You can also provide the information in the command line:

```bash
akit --project_name <yourproject_name> --openai_key <sk-XX> --openai_org <theorgid> --path <path_to_project>
```

Then you can edit your agent in the created folder. The agent will be already running in and in auto-reload mode. 

### Stop/Start/rebuild 

```bash
akit stop
akit start
akit rebuild
akit down
akit up
```

You will have access to the following tools with local urls in your browser:

- AgentKit: http://localhost:9090/api/v1/docs : For testing your argent live
- Jaeger: http://localhost:16686: For tracing your agent
- Dozzle: http://localhost:9999: For monitoring your agent logs





