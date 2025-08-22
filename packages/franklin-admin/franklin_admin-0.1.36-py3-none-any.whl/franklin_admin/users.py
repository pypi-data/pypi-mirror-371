import click
import subprocess
import sys
import os
from subprocess import DEVNULL, STDOUT, PIPE
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Tuple, List, Dict, Callable, Any
import requests

from franklin_cli import crash
from franklin_cli import config as cfg
from franklin_cli import utils
from franklin_cli import terminal as term
from franklin_cli import gitlab
from franklin_cli.logger import logger
from . import encrypt
from franklin_educator import git

from rapidfuzz import process, fuzz
import unicodedata
import re



perm = {
    'No access': 0,
    'Reporter': 20,
    'Maintainer': 40,
    'Owner': 50,
    'Admin': 60
}

permission_levels = {
    'guest': (perm['Reporter'], perm['Reporter'], perm['Reporter']),
    'ta': (perm['Reporter'], perm['Maintainer'], perm['Maintainer']),
    'prof': (perm['Reporter'], perm['Owner'], perm['Owner']),
    'admin': (perm['Admin'], perm['Admin'],  perm['Admin']),
}
# mbg aliases
permission_levels['vip'] = permission_levels['prof']
permission_levels['inst'] = permission_levels['ta']



def invite_user_with_permissions(user_email: str, group_id: int, access_level: int, api_token: str):

    members: Dict[int, Any] = gitlab.get_group_members(group_id, api_token)
    logger.debug('existing members {members}')

    headers = {"PRIVATE-TOKEN": api_token, "Content-Type": "application/json"}

    logger.debug(f'Email user invitation to {user_email} to group {group_id} with access {access_level}')

    url = f"https://{cfg.gitlab_domain}/api/v4/groups/{group_id}/invitations"
    response = requests.post(url, headers=headers, json={
        "email": user_email,
        "access_level": access_level
    })
    response.raise_for_status()
    # if response.status_code == 200:

    print("Member added and permissions set successfully.")
    # else:
    #     print(f"Error {response.status_code}: {response.json()}")


def update_group_permissions(user_id: int, group_id: int, access_level: int, api_token: str):

    members: Dict[int, Any] = gitlab.get_group_members(group_id, api_token)
    logger.debug('existing members {members}')

    headers = {"PRIVATE-TOKEN": api_token, "Content-Type": "application/json"}
    if user_id not in members:
        logger.debug(f'Adding usr to group {user_id}, {group_id}, {access_level}')

        url = f"https://{cfg.gitlab_domain}/api/v4/groups/{group_id}/members"
        response = requests.post(url, headers=headers, json={
            "user_id": user_id,
            "access_level": access_level
        })
        if response.status_code == 200:
            print("Member added and permissions set successfully.")
        else:
            print(f"Error {response.status_code}: {response.json()}")
    else:
        logger.debug(f'Updating access to group {user_id}, {group_id}, {access_level}')
        
        url = f"https://{cfg.gitlab_domain}/api/v4/groups/{group_id}/members/{user_id}"
        response = requests.put(
            url, 
            headers=headers, 
            json={"access_level": access_level}
            )
        if response.status_code != 200:
        #     print("Access level updated successfully.")
        # # elif response.status_code == 404:
        # #     print("User is not a member of the project.")
        # else:
            print(f"Error {response.status_code}: {response.json()}")


def invite_user(user_email, role, course, listed_course_name, api_token, project=None):

    group_id: int = gitlab.get_group_id(cfg.gitlab_group, api_token)
    subgroup_id: int = gitlab.get_group_id(course, api_token)

    # term.echo(f"Updating permissions for user '{user_name}' "
    #           f"({get_user_info(user_id, api_token)['name']}) "
    #           f"with role '{role}' in course '{listed_course_name}' "
    #           f"(repo: {course}).")
    term.secho()
    term.secho(f"Email user invitation")
    term.secho(f'To user:')
    term.secho(f"  email: {user_email} ", fg='green')
    term.secho(f'as:')
    term.secho(f"  {role}", fg='green')
    term.secho(f'for course:')
    name = f', ({listed_course_name})' if listed_course_name else ''
    term.secho(f'  {course}' + name, fg='green')
    term.secho()
    click.confirm("Do you want to continue?", abort=True, default=True)

    group_perm, subgroup_perm, project_perm = permission_levels[role]

    invite_user_with_permissions(user_email, group_id, group_perm, api_token)
    invite_user_with_permissions(user_email, subgroup_id, subgroup_perm, api_token)


def update_permissions(user_id, role, course, listed_course_name, api_token, project=None):

    group_id: int = gitlab.get_group_id(cfg.gitlab_group, api_token)
    subgroup_id: int = gitlab.get_group_id(course, api_token)

    # term.echo(f"Updating permissions for user '{user_name}' "
    #           f"({get_user_info(user_id, api_token)['name']}) "
    #           f"with role '{role}' in course '{listed_course_name}' "
    #           f"(repo: {course}).")
    term.secho()
    term.secho(f"Granting access to")
    term.secho(f'To user:')
    term.secho(f"  {user_id} ({gitlab.get_user_info(user_id, api_token)['name']})", fg='green')
    term.secho(f'as:')
    term.secho(f"  {role}", fg='green')
    term.secho(f'for course:')
    name = f', ({listed_course_name})' if listed_course_name else ''
    term.secho(f'  {course}' + name, fg='green')
    term.secho()
    click.confirm("Do you want to continue?", abort=True, default=True)

    group_perm, subgroup_perm, project_perm = permission_levels[role]

    update_group_permissions(user_id, group_id, group_perm, api_token)
    update_group_permissions(user_id, subgroup_id, subgroup_perm, api_token)

    # if project_id is not None:
    #     project_id = get_project_id(project, group_id)
    #     update_group_permissions(user_id, project_id, project_perm)

    # # If you receive a 404 error, the user is not yet a member of the project. In that case, use:
    # # POST /projects/:id/members to add a new user
    # url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/members"
    # response = requests.post(url, headers=headers, json={
    #     "user_id": USER_ID,
    #     "access_level": ACCESS_LEVEL
    # })


# clone password repo into franklin-admin/data/passwords dir and sync that way
# call th password  repo _passwords and skip all 

# add three levels of access: admin, vip, ta


def create_impersonation_token(user_id: int, admin_api_token: str):

    response = requests.post(
        f"https://{cfg.gitlab_domain}/api/v4/users/{user_id}/impersonation_tokens",
        headers={
            "PRIVATE-TOKEN": admin_api_token
            },
        json= {
            "name": 'api_access_token',
            "scopes": ["api", "read_repository", "write_repository"], 
            "expires_at": "2025-12-31"  # optional
            }
    )

    if response.status_code == 201:
        token_info = response.json()
        print("Token created:")
        print(f"Token: {token_info['token']}")
        print(f"Scopes: {token_info['scopes']}")
        return token_info['token']
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


@click.group(cls=utils.AliasedGroup)
def user():
    """Admin commands for access control.
    """


@user.group(cls=utils.AliasedGroup)
def password():
    """Admin commands for admin tokens.
    """

# add_admin(user, password, api_token, admin, admin_password)

# set_password(user, password, admin, admin_password)

# set_token(user, password)


@password.command('set')
@click.argument("user")
@click.argument("password")
@click.option('--admin', prompt=True, help='User name')
@click.option('--password', prompt=True, hide_input=True, help='Password')
@click.option('--overwrite', default=False, help='Overwrite existing token if it exists.')
def set_password(user, password, admin, admin_password, overwrite):
    admin_api_token = encrypt.get_api_token(admin, admin_password)
    user_id = gitlab.get_user_id(user, admin_api_token)
    user_api_token = create_impersonation_token(user_id, admin_api_token)
    try:
        encrypt.store_encrypted_token(user, password, user_api_token, overwrite=overwrite)
    except FileExistsError as e:
        term.secho(f"Error storing token for user {user}: {e}", fg="red")


@password.command('change')
@click.option('--user', prompt=True, help='User name')
@click.option('--password', prompt=True, hide_input=True, help='Password')
@click.option('--new-password', prompt=True, hide_input=True, help='New password')
@click.option('--new-password-repeat', prompt=True, hide_input=True, help='New password repeated')
def change_password(user, password, new_password, new_password_repeat):
    if new_password != new_password_repeat:
        term.secho("New passwords do not match. Password not changed.")
        click.Abort()
    api_token = encrypt.get_api_token(user, password)
    encrypt.store_encrypted_token(user, new_password, api_token, overwrite=True)




# @password.command('get')
# @click.option('--admin', prompt=True, help='User name')
# @click.option('--password', prompt=True, hide_input=True, help='Password')
# @click.argument("user")
# def get_password(admin, password, user):
#     """Stores an encrypted token for the user.
#     """
#     api_token = encrypt.decrypt(admin, password)
#     term.echo(f'Stored personal access token: {api_token}')



@user.group(cls=utils.AliasedGroup)
def token():
    """Admin commands for admin tokens.
    """


@token.command('set')
@click.option('--user', prompt=True, help='User name')
@click.option('--password', prompt=True, hide_input=True, help='Password')
@click.option('--api-token', prompt=True, hide_input=True, help='User API token')
def set_token(user, password, api_token):
    """Stores an encrypted token for the user.
    """
    encrypt.store_encrypted_token(user, password, api_token, overwrite=True)



# import pandas as pd
# with open('users.tsv', 'w') as f:
#     for line in f:
#         user_name, user_password = line.split()
#         try:
#             token = encrypt.get_api_token(user_name, user_password)
#             print(f"Toke for '{user_name}' already exists")
#         except FileNotFoundError as e:
#            utils.run_cmd(f"franklin password --user {user_name} --password {user_password}")
#         print(f"Created token for '{user_name}'")


@token.command('get')
@click.option('--user', prompt=True, help='User name')
@click.option('--password', prompt=True, hide_input=True, help='Password')
def get_token(user, password):
    """Stores an encrypted token for the user.
    """
    api_token = encrypt.get_api_token(user, password)
    term.echo(f'Stored personal access token: {api_token}')


@user.command()
@click.option('--user', prompt=True, help='User name')
@click.option('--password', prompt=True, hide_input=True, help='Password')
@click.argument("query", nargs=-1)
def finger(query, user, password):
    """Find users in GitLab by name.
    """
    api_token = encrypt.get_api_token(user, password)
    
    users = []
    page = 1
    while True:
        response = requests.get(
            f"http://{cfg.gitlab_domain}/api/v4/users",
            headers = {"PRIVATE-TOKEN": api_token},
            params={"per_page": 100, "page": page}
        )
        data = response.json()
        if not data:
            break
        users.extend(data)
        page += 1

    # Output user info
    user_names = []
    names = []
    for user in users:
        user_names.append(user['username'])
        names.append(user['name'])

    def normalize(name):
        name = name.lower()
        name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
        name = re.sub(r"[^\w\s]", "", name)
        return name.strip()

    normalized_names = [normalize(n) for n in names]

    for q in query:
        term.echo()
        query_normalized = normalize(q)
        # match = process.extractOne(query_normalized, normalized_names, scorer=fuzz.WRatio)
#        match = process.extractOne(query_normalized, normalized_names, scorer=fuzz.WRatio, score_cutoff=90.0)
        matches = process.extract(query_normalized, normalized_names, scorer=fuzz.WRatio, score_cutoff=80.0, limit=5)
        prev = 0
        if matches:
            for match in matches:
                name, score, index = match
                # term.secho(str(round(score, 1)).ljust(4), nl=False)
                term.secho(user_names[index].ljust(9), fg='green', nl=False)
                term.secho(names[index])
                if score - prev > 1:
                    break
                prev = score
        else:
            print(f"No users found matching '{q}'")
    term.echo()


@user.group(cls=utils.AliasedGroup)
def grant():
    """Commands for granting/revoking user permissions.
    """

def _grant_role(role, admin, password, user_name=None, user_email=None, course=None):

    api_token: str = encrypt.get_api_token(admin, password)

    user_id = None
    if user_name is not None:
        user_id = gitlab.get_user_id(user_name, api_token)

    if not user_id and not user_email:
        term.secho("User not found and no email provided for invite.", fg='red')
        sys.exit(1)

    listed_course_name = None
    if course is None:
        course, listed_course_name = gitlab.pick_course()

    if user_id is None:
        if user_email is None:
            term.secho("User not found and no email provided for invite.", fg='red')
            sys.exit(1)
        invite_user(user_email, role, course, listed_course_name, api_token)
    else:
        update_permissions(user_id, role, course, listed_course_name, api_token)


@grant.command('guest')
@click.option('--admin', prompt=True, help='Admin user')
@click.option('--password', prompt=True, hide_input=True, help='Admin password')
@click.option('--course', '-c', required=False, help='Course name')
@click.option('--user-name', '-u', required=False, help='Username')
@click.option('--user-email', '-e', required=False, help='User email for invite')
@crash.crash_report
@git.gitlab_ssh_access
def grant_ta_role(admin, password, user_name=None, user_email=None, course=None):
    """Grant guest permissions to a user (read only).
    """
    _grant_role("guest", admin=admin, password=password, user_name=user_name, user_email=user_email, course=course)


@grant.command('ta')
@click.option('--admin', prompt=True, help='Admin user')
@click.option('--password', prompt=True, hide_input=True, help='Admin password')
@click.option('--course', '-c', required=False, help='Course name')
@click.option('--user-name', '-u', required=False, help='Username')
@click.option('--user-email', '-e', required=False, help='User email for invite')
@crash.crash_report
@git.gitlab_ssh_access
def grant_ta_role(admin, password, user_name=None, user_email=None, course=None):
    """Grant guest permissions to a user (read only).
    """
    _grant_role("ta", admin=admin, password=password, user_name=user_name, user_email=user_email, course=course)


@grant.command('prof')
@click.option('--admin', prompt=True, help='Admin user')
@click.option('--password', prompt=True, hide_input=True, help='Admin password')
@click.option('--course', '-c', required=False, help='Course name')
@click.option('--user-name', '-u', required=False, help='Username')
@click.option('--user-email', '-e', required=False, help='User email for invite')
@crash.crash_report
@git.gitlab_ssh_access
def grant_ta_role(admin, password, user_name=None, user_email=None, course=None):
    """Grant guest permissions to a user (read only).
    """
    _grant_role("prof", admin=admin, password=password, user_name=user_name, user_email=user_email, course=course)


# @grant.command('ta')
# @click.argument('user_name')
# @click.option('--user', prompt=True, help='Admin user')
# @click.option('--password', prompt=True, hide_input=True, help='Admin password')
# @click.option('--course', '-c', required=False, help='Course name')
# @crash.crash_report
# @git.gitlab_ssh_access
# def grant_ta_role(user_name, user, password, course=None):
#     """Grant TA permissions to a user.
#     """
#     listed_course_name = None
#     if course is None:
#         course, listed_course_name = gitlab.pick_course()
#     update_permissions(user_name, 'ta', course, listed_course_name, user, password)


# @grant.command('prof')
# @click.argument('user_name')
# @click.option('--user', prompt=True, help='Admin user')
# @click.option('--password', prompt=True, hide_input=True, help='Admin password')
# @click.option('--course', '-c', required=False, help='Course name')
# @crash.crash_report
# @git.gitlab_ssh_access
# def grant_prof_role(user_name, user, password, course=None):
#     """Grant course responsible permissions to a user.
#     """
#     listed_course_name = None
#     if course is None:
#         course, listed_course_name = gitlab.pick_course()    
#     update_permissions(user_name, 'prof', course, listed_course_name, user, password)


#     create_impersonation_token(gitlab.get_user_id(user_name, encrypt.get_api_token(user, password)))


# #    generate_password = 
#     if not user_exists()
#         user_password = generate_password()
#         set_password(user_name, user_password, admin, admin_password):

#     print("CreatedUser: {user_name} Password: {user_password}")


#set_password


# @grant.command('admin')
# @click.argument('user')
# @click.option('--password', prompt=True, hide_input=True,
#               confirmation_prompt=False, help='Admin password')
# @click.option('course', '--course', '-c', required=False, help='Course name')
# @crash.crash_report
# @git.gitlab_ssh_access
# def grant_admin_role(user, password, course=None):
#     """Grant admin permissions to a user.
#     """
#     update_permissions(user, 'prof', course, password)




# # Example usage:
# if __name__ == "__main__":
#     path = "admin_token.enc"
#     # First time: store_encrypted_token(path)
#     # Later use:
#     decrypted_token = load_and_decrypt_token(path)
#     print(f"Decrypted API token: {decrypted_token}")



# @click.option('--admin-password', required=False, prompt=True, hide_input=True)

# if admin_password == "expected_password":

    



# headers = {
#     "Private-Token": ADMIN_TOKEN,
#     "Content-Type": "application/json"
# }

# def add_user_to_group(group_id, user_id, access_level):
#     url = f"{GITLAB_URL}/api/v4/groups/{group_id}/members"
#     data = {
#         "user_id": user_id,
#         "access_level": access_level
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response.json()

# def add_user_to_subgroup(subgroup_id, user_id, access_level):
#     url = f"{GITLAB_URL}/api/v4/groups/{subgroup_id}/members"
#     data = {
#         "user_id": user_id,
#         "access_level": access_level
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response.json()

# def add_user_to_project(project_id, user_id, access_level):
#     url = f"{GITLAB_URL}/api/v4/projects/{project_id}/members"
#     data = {
#         "user_id": user_id,
#         "access_level": access_level
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response.json()


# perm = {
#     'No access': 0,
#     'Reporter': 20,
#     'Maintainer': 40,
#     'Owner': 50,
#     'Admin': 60
# }

# permission_levels = {
#     'ta': (perm['Reporter'], perm['Maintainer']),
#     'prof': (perm['Reporter'], perm['Owner']),
#     'admin': (perm['Admin'], perm['Admin']),
# }

# def give_permissions(group_id, subgroup_id, user_id, role):
#     """
#     Assigns TA permissions to a user in a group.
#     """
#     group_access, subgroup_access = permission_levels[role]
#     group_response = add_user_to_group(group_id, user_id, group_access)
#     print("Group response:", group_response)
#     subgroup_response = add_user_to_subgroup(subgroup_id, user_id, subgroup_access)
#     print("Subgroup response:", subgroup_response)

# # Replace these variables with your actual values
# GITLAB_URL = "https://gitlab.au.dk"
# PRIVATE_TOKEN = "your_personal_access_token"
# GROUP_ID = "your_group_id"
# SUBGROUP_ID = "your_subgroup_id"
# PROJECT_ID = "your_project_id"
# USER_ID = "user_id_to_add"
# ACCESS_LEVEL = 30  # Developer access level; see GitLab documentation for other levels


# # group_response = add_user_to_group(GROUP_ID, USER_ID, ACCESS_LEVEL)
# # print("Group response:", group_response)

# # subgroup_response = add_user_to_subgroup(SUBGROUP_ID, USER_ID, ACCESS_LEVEL)
# # print("Subgroup response:", subgroup_response)

# # project_response = add_user_to_project(PROJECT_ID, USER_ID, ACCESS_LEVEL)
# # print("Project response:", project_response)

# project_response = add_user_to_project('franklin', 'genomic-thinking', perm['Admin'])
# print("Project response:", project_response)

# ##########


# import requests

# # GitLab instance and authentication
# GITLAB_URL = "https://gitlab.example.com"
# API_TOKEN = "your_private_token"
# PROJECT_ID = 12345
# USER_ID = 67890

# # New access level
# ACCESS_LEVEL = 40  # Maintainer

# # API endpoint to update existing member
# url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/members/{USER_ID}"

# headers = {
#     "PRIVATE-TOKEN": API_TOKEN,
#     "Content-Type": "application/json"
# }

# payload = {
#     "access_level": ACCESS_LEVEL
# }

# # Execute request
# response = requests.put(url, headers=headers, json=payload)

# # Output response
# if response.status_code == 200:
#     print("Access level updated successfully.")
# elif response.status_code == 404:
#     print("User is not a member of the project.")
# else:
#     print(f"Error {response.status_code}: {response.json()}")


# # If you receive a 404 error, the user is not yet a member of the project. In that case, use:

# # POST /projects/:id/members to add a new user
# url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/members"
# response = requests.post(url, headers=headers, json={
#     "user_id": USER_ID,
#     "access_level": ACCESS_LEVEL
# })



# # https://docs.gitlab.com/ee/api/members.html#edit-a-project-member
# # https://docs.gitlab.com/ee/api/members.html#add-a-member-to-a-project-or-group



