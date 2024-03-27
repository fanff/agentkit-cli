

import fileinput
import glob
import io
import os
import shutil
import click
from importlib.resources import files

CONNEXION_LINES =[
("AgentKit","http://localhost:3000","For testing your argent live"),
("API","http://localhost:9090/api/v1/docs","For testing with the API directly"),
("Jaeger","http://localhost:16686","For tracing execution of your agent"),
("Dozzle","http://localhost:9999","For monitoring your agent logs"),
]

GREEN = '\033[92m'  # Green text
RESET = '\033[0m'   # Reset attributes
BOLD = '\033[1m'    # Bold text


def echo_links():
    click.echo(f"{BOLD}Common connexion lines to use : {RESET}\n")
    for name,link,desc in CONNEXION_LINES:
        click.echo(f"{GREEN}{name}{RESET} : {link} {desc}")
    click.echo("")

def echo_suggested_commands():
    click.echo(f"{BOLD}Suggested commands : {RESET}\n")
    all_commands = {
        "akit init":"Initialize your project",
        "akit up":"Start your project containers",
        "akit down":"Stop your project",
        "akit build":"Build your project",
        "akit ps":"Get current running containers",
        "akit help":"Get information about your project",
    }
    
    for cmd,desc in all_commands.items():
        click.echo(f"{GREEN}{cmd}{RESET} : {desc}")
    click.echo("")

def replace_line(file_name, prefix, new_line):
    # Placeholder to track if replacement has occurred
    replaced = False
    # Use fileinput to edit in place; with inplace=1, it creates a backup by default
    with fileinput.FileInput(file_name, inplace=True) as file:
        for line in file:
            # Check if line starts with prefix and hasn't been replaced yet
            if line.startswith(prefix) and not replaced:
                print(new_line)
                replaced = True
            else:
                print(line, end='')

def run_command(command):
    import subprocess
    # run process 
    run_completed = subprocess.run(command, shell=True, capture_output=True)
    if run_completed.returncode == 0:    
        return run_completed.stdout.decode('utf-8')
    else:
        return f"Error running: {command} \n{run_completed.stdout.decode('utf-8')} \n{run_completed.stderr.decode('utf-8')}"

@click.group()
def cli():
    pass

@cli.command()
@click.option('--path', default='.', help='The directory to initialize the project in.')
@click.option('--project_name', prompt=True, help='The name of the project')
@click.option('--openai_key', prompt=True, help='The openai key')
@click.option('--openai_org', prompt=True, help='The openai organization')
def init(path,project_name,openai_key,openai_org):
    """initialize your project"""
    # request the user to input the project name
    click.echo(f'Project initialized in {path}, with the name {project_name}')

    # Grab a particular git remote, head only, checkout only
    branch_name="int"
    repo_url="https://github.com/fanff/agentkit.git"
    # if the directory exists, remove it
    if os.path.exists(f"{path}/agentkit"):
        shutil.rmtree(f"{path}/agentkit")
    
    # clone the repo
    os.system(f"git clone --depth 1 {repo_url} -b {branch_name}")

    # Copy paste a .env.example into a .env file locally agentkit/.env.example .envbackend
    shutil.copyfile(f"{path}/agentkit/.env.example", f"{path}/.envbackend")
    shutil.copyfile(f"{path}/agentkit/frontend/.env.example", f"{path}/.envfrontend")

    # Copy the sample agent configuration in a fresh directory
    dest_path = f"{path}/{project_name}_agentconfig"
    mounted_dest_path = f"/{project_name}_agentconfig" # docker volume path , as seen from inside the container

    os.makedirs(dest_path, exist_ok=True)

    # manage the text documents directory
    docs_path = f"{path}/{project_name}_textdocuments"
    mounted_docs_path = f"/{project_name}_textdocuments" # docker volume path , as seen from inside the container
    os.makedirs(docs_path, exist_ok=True)

    replace_line(".envbackend", "PDF_TOOL_DATA_PATH", f"PDF_TOOL_DATA_PATH=/{mounted_docs_path}/")
    replace_line(".envbackend", "EXTRACTION_CONFIG_PATH", f"EXTRACTION_CONFIG_PATH=/{mounted_dest_path}/extraction.yml")

    # Access a YAML file
    yaml_path = files('agentkitcli.tools_bootstrap') # name of a module here

    for d in yaml_path.iterdir():
        if str(d).endswith('.yaml') or str(d).endswith('.yml'):
            shutil.copy(d, f"{dest_path}/{d.name}")

    # NEXTAUTH_SECRET=$(openssl rand -hex 32)
    # python version:
    import secrets
    nextauth_secret = secrets.token_hex(32)

    replace_line(".envbackend", "OPENAI_API_KEY", f"OPENAI_API_KEY={openai_key}")
    replace_line(".envbackend", "OPENAI_ORGANIZATION", f"OPENAI_ORGANIZATION={openai_org}")
    replace_line(".envbackend", "NEXTAUTH_SECRET", f"NEXTAUTH_SECRET={nextauth_secret}")
    replace_line(".envbackend", "AGENT_CONFIG_PATH", f"AGENT_CONFIG_PATH=/{dest_path}/agent.yml")
    replace_line(".envbackend", "PROJECT_NAME", f"PROJECT_NAME={project_name}")

    replace_line(".envfrontend", "NEXTAUTH_SECRET", f"NEXTAUTH_SECRET={nextauth_secret}")
    replace_line(".envfrontend", "NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_API_URL=http://localhost:9090/api/v1")

    # copy the .envfrontend to the frontend directory 
    shutil.copyfile(".envfrontend", f"{path}/agentkit/frontend/.env")

    # copy the compose.yml.tmpl to compose.yml
    compose_file = yaml_path.joinpath('compose.yml.tmpl')
    compose_content = compose_file.read_text()
    compose_content = compose_content.replace("PROJECT_NAME", project_name)
    with open(f"{path}/compose.yml", "w") as f:
        f.write(compose_content)


    ans = click.prompt("Do you want to build docker images now ? [Y/n]",default="Y")
    if ans.lower() == "y":
        # run dockbuild 
        run_command("docker-compose --env-file .envbackend build fastapi_server")
        run_command("docker-compose --env-file .envfrontend build nextjs_server")
        # run docker-compose up
        run_command("docker-compose --env-file .envbackend up -d")


    click.echo(f"{BOLD}You can now access your agent : {RESET}\n")
    echo_links()
    
    echo_suggested_commands()

    click.echo("Your agent configuration is located in : ")
    click.echo(f"{BOLD}{GREEN}{dest_path}/{RESET}")


    


@cli.command()
@click.option('--envfile', default='.envbackend',  help='The env file to use')
@click.argument('extra_docker_args', nargs=-1)
def down(envfile,extra_docker_args):
    """Stop and clean up."""
    extra = " ".join(extra_docker_args)
    run_command(f"docker-compose --env-file {envfile} down {extra}")

@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
@click.argument('extra_docker_args', nargs=-1)
def up(envfile,extra_docker_args):
    """Start the environment."""
    # copy the .envfrontend to the frontend directory (necessary at build time)
    shutil.copyfile(f"{envfile}", "./agentkit/frontend/.env")
    extra = " ".join(extra_docker_args)
    run_command(f"docker-compose --env-file {envfile} up -d {extra}")

@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
def build(envfile):
    """Build all the docker images."""
    run_command(f"docker-compose --env-file {envfile} build fastapi_server")

    # copy the .envfrontend to the frontend directory (necessary at build time )
    shutil.copyfile(f"{envfile}", "./agentkit/frontend/.env")
    run_command(f"docker-compose --env-file {envfile} build nextjs_server")


@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
@click.argument('extra_docker_args', nargs=-1)
def ps(envfile, extra_docker_args):
    """Show the running containers."""
    extra = " ".join(extra_docker_args)
    r = run_command(f"docker-compose --env-file {envfile} ps {extra}")
    click.echo(r)


@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
@click.argument('container', nargs=1)
def restart(envfile, container):
    """Show the running containers."""
    r = run_command(f"docker-compose --env-file {envfile} restart {container}")
    click.echo(r)

@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
def ingest(envfile):
    """Ingest the documents."""
    # run a command in the fastapi container
    run_command(f"docker-compose --env-file {envfile} exec fastapi_server python app/document_ingestion.py")

@cli.command()
def help(envfile):
    echo_links()
    echo_suggested_commands()

def main():
    cli()
    
if __name__ == '__main__':
    cli()