# AgentKit Cli

AgentKit Cli is a tool to help you get started with the AgentKit platform. It will create a new project for you and set up the necessary files and directories to get you started.

## Installation

To install the akit-bootstrap tool, you can use pip and install globally in your system:

```bash
pip install -U git+https://github.com/fanff/agentkit-cli
# akit is now installed
```


## New Project creation

To create a new project, you can use the following command, in an empty directory:

```bash
akit init 
```

Akit will automatically query you if there is missing information. 
You can also provide the information in the command line:

```bash
akit --project_name <yourproject_name> --openai_key <sk-XX> --openai_org <theorgid> --path <path_to_project>
```

Then you can edit your agent in the created folder. The agent will be already running in and in auto-reload mode. 


You will have access to the following tools with local urls in your browser:

* AgentKit : http://localhost:3000 For testing your argent live
* API : http://localhost:9090/api/v1/docs For testing with the API directly
* Jaeger : http://localhost:16686 For tracing execution of your agent
* Dozzle : http://localhost:9999 For monitoring your agent logs

Suggested commands : 




A default agent configuration structure is ready for you to edit:

```
<project_name>_agentconfig/ 
│   agent.yml  # The main agent configuration file
│   tools.yml  # The Tools configuration file
│   extraction.yml # The extraction configuration file for ingesting documents
compose.yml
```


## Document ingestion

[in construction] To start the document ingestion, you can use the following process:

1. Put your documents inside the `<project_name>_textdocuments` folder. 
2. Edit the `extraction.yml` file to define the extraction process.
3. Start the ingestion process with the `akit ingest` command.

```bash
akit ingest 
```

### Stop/Start/rebuild 
* `akit init` : Initialize your project
* `akit up` : Start your project containers
* `akit down` : Stop your project
* `akit build` : Build your project
* `akit ps` : Get current running containers
* `akit help` : Get information about your project


# add the indexing of the files command 



