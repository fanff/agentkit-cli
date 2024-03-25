

import fileinput
import glob
import os
import shutil
import click
from importlib.resources import files

CONNEXION_LINES ="""
* AgentKit: http://localhost:9090/api/v1/docs : For testing your argent live
* Jaeger: http://localhost:16686: For tracing your agent
* Dozzle: http://localhost:9999: For monitoring your agent logs
"""

GREEN = '\033[92m'  # Green text
RESET = '\033[0m'   # Reset attributes
BOLD = '\033[1m'    # Bold text

def echo_suggested_commands():
    click.echo(f"{BOLD}Suggested commands : {RESET}\n")
    all_commands = {
        "akit init":"Initialize your project",
        "akit up":"Start your project",
        "akit down":"Stop your project",
        "akit build":"Build your project",
        "akit info":"Get information about your project",
    }
    
    for cmd,desc in all_commands.items():
        click.echo(f"{GREEN}{cmd}{RESET} : {desc}")

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
    branch_name="feature/bettermonitoring"
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

    os.makedirs(dest_path, exist_ok=True)

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
    replace_line(".envbackend", "EXTRACTION_CONFIG_PATH", f"EXTRACTION_CONFIG_PATH=/{dest_path}/extraction.yml")
    replace_line(".envbackend", "PROJECT_NAME", f"PROJECT_NAME={project_name}")

    # copy the compose.yml.tmpl to compose.yml
    compose_file = yaml_path.joinpath('compose.yml.tmpl')
    compose_content = compose_file.read_text()
    compose_content = compose_content.replace("PROJECT_NAME", project_name)
    with open(f"{path}/compose.yml", "w") as f:
        f.write(compose_content)


    ans = click.prompt("Do you want to build docker images now ? [Y/n]",default="Y")
    if ans.lower() == "y":
        # run dockbuild 
        os.system("docker-compose --env-file .envbackend build")
        # run docker-compose up
        os.system("docker-compose --env-file .envbackend up -d")


    click.echo(f"{BOLD}You can now access your agent : {RESET}\n")
    click.echo(CONNEXION_LINES)
    
    echo_suggested_commands()

    click.echo("Your agent configuration is located in : ")
    click.echo(f"{BOLD}{GREEN}{dest_path}{RESET}")


    


@cli.command()
@click.option('--envfile', default='.envbackend',  help='The env file to use')
def down(envfile):
    os.system(f"docker-compose --env-file {envfile} down")

@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
def up(envfile):
    os.system(f"docker-compose --env-file {envfile} up -d")

@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
def build(envfile):
    os.system(f"docker-compose --env-file {envfile} build")



@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
def ps(envfile):
    os.system(f"docker-compose --env-file {envfile} ps")


@cli.command()
@click.option('--envfile', default='.envbackend', help='The env file to use')
def help(envfile):

    click.echo(f"{BOLD}Common connexion lines to use : {RESET}\n")

    click.echo(CONNEXION_LINES)
    echo_suggested_commands()
def main():
    cli()
    
if __name__ == '__main__':
    cli()