import shutil, os

try:
    import asyncio
except:
    os.system('pip install asyncio')
try:
    import discord
except:
    os.system('pip install discord')
try:
    from discord_components import DiscordComponents, Button, ButtonStyle
except:
    os.system('pip install discord-components')
try:
    from discord_webhook import DiscordWebhook
except:
    os.system('pip install discord-webhook')



token = '12345'  # 봇토큰
guild_id = '12345'  # 서버아이디
category_id = '12345'  # 카테고리아이디 (아무 채널 없는 새 카테고리)



intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
DiscordComponents(client)


@client.event
async def on_connect():
    if not os.path.isdir('data'):
        os.mkdir('data')
    print(client.user)


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild is None:
        directory = f'data/{message.author.id}'

        if not os.path.isdir(directory):
            guild = client.get_guild(int(guild_id))
            os.mkdir(directory)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }

            channel = await guild.create_text_channel(name=message.author.id,
                                                      category=client.get_channel(int(category_id)),
                                                      overwrites=overwrites)
            webhook_url = await channel.create_webhook(name=message.author)

            with open(f'{directory}/webhook.txt', 'w') as f:
                f.write(webhook_url.url)
            with open(f'{directory}/channel.txt', 'w') as f:
                f.write(str(channel.id))

            e = discord.Embed(description='', colour=discord.Colour.green())
            e.set_footer(text=f'{message.author}의 문의')
            await channel.send(embed=e,
                               components=[Button(style=ButtonStyle.red, label="닫기", custom_id='close-admin')])

            webhook_msg = DiscordWebhook(url=webhook_url.url, content=message.content)
            webhook_msg.execute()

            e = discord.Embed(description='', colour=discord.Colour.green())
            e.set_footer(text='문의가 접수되었습니다.\n추가 문의사항을 남겨주세요.')
            await message.reply(embed=e,
                                components=[Button(style=ButtonStyle.red, label="닫기", custom_id='close-user')])
        else:
            with open(f'{directory}/webhook.txt', 'r') as f:
                webhook_url = str(f.read())

            webhook_msg = DiscordWebhook(url=webhook_url, content=message.content)
            webhook_msg.execute()


    elif message.channel.category.id == int(category_id):
        target = client.get_user(int(message.channel.name))
        try:
            await target.send(message.content)
        except:
            await message.reply('> 메시지 발송을 실패하였습니다')
            return


@client.event
async def on_button_click(interaction):
    if interaction.custom_id == "close-user":
        if not os.path.isdir(f'data/{interaction.user.id}'):
            return
        
        with open(f'data/{interaction.user.id}/channel.txt') as f:
            channel_id = f.read()
        own_channel = client.get_channel(int(channel_id))

        shutil.rmtree(f'data/{interaction.user.id}')
        e = discord.Embed(description='', colour=discord.Colour.red())
        e.set_footer(text='문의가 종료되었습니다.')
        await interaction.respond(embed=e)

        await own_channel.edit(name=f'{interaction.user.id}-closed')
        e = discord.Embed(description='', colour=discord.Colour.red())
        e.set_footer(text='문의가 종료되었습니다.\n아래 버튼을 눌러 채널을 삭제해주세요.')
        await own_channel.send(embed=e, components=[Button(style=ButtonStyle.red, label="채널 삭제", custom_id='remove')])

    if interaction.custom_id == "close-admin":
        target_id = interaction.channel.name
        target = client.get_user(int(target_id))
        shutil.rmtree(f'data/{target_id}')

        e = discord.Embed(description='', colour=discord.Colour.red())
        e.set_footer(text='문의가 종료되었습니다.')
        await target.send(embed=e)

        await interaction.channel.edit(name=f'{interaction.user.id}-closed')
        e = discord.Embed(description='', colour=discord.Colour.red())
        e.set_footer(text='문의가 종료되었습니다.\n아래 버튼을 눌러 채널을 삭제해주세요.')
        await interaction.channel.send(embed=e,
                                       components=[Button(style=ButtonStyle.red, label="채널 삭제", custom_id='remove')])

    if interaction.custom_id == "remove":
        e = discord.Embed(description='', colour=discord.Colour.red())
        e.set_footer(text='10초 후 채널이 삭제됩니다')
        await interaction.respond(embed=e)

        await asyncio.sleep(10)
        await interaction.channel.delete()


client.run(token)
