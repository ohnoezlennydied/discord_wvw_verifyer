#!/usr/bin/env python
import discord
import json

import gw2api.v2
import re

import requests

client = discord.Client()
config_file = open("config.json", "r")
config = json.load(config_file)
api_regex = "([A-Z,0-9]){8}-(([A-Z,0-9]){4}-){3}([A-Z,0-9]){20}-(([A-Z,0-9]){4}-){3}([A-Z,0-9]){12}"


@client.event
async def on_member_join(member):
    await client.send_message(member, config["welcome_message"])


@client.event
async def on_message(message):
    server = discord.utils.get(client.servers, id=config["server_id"])
    if message.content.startswith("!verify"):
        api_key = message.content.split(" ")[1]
        if re.match(api_regex, api_key) and len(api_key) == 72:
            gw2api.v2.account.set_token(api_key)
            try:
                gw2_account_data = gw2api.v2.account.get()
                account_world = gw2api.v2.worlds.get_one(gw2_account_data["world"])["name"]
                role = discord.utils.get(server.roles, name=config["roles"][account_world])
                user = discord.utils.get(server.members, name=re.sub(r"#\d{4}", "", str(message.author)))
                try:
                    await client.add_roles(user, role)
                    await client.send_message(message.channel, "Successfully added role {0}".format(role.name))
                except discord.Forbidden:
                    await client.send_message(message.channel, "I don't have permission to add roles.")
            except requests.exceptions.HTTPError:
                await client.send_message(message.channel, 'It seams your api key is not valid.')
        else:
            await client.send_message(message.channel, 'It seams your api key has a wrong format.')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(config["bot_token"])
