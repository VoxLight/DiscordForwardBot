"""
   Copyright 2023 VoxLight

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from nextcord.ext import commands
import nextcord
from lib import database


class Forwarder(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.db = database.get_db()
        print("Forwarder cog loaded")

    async def begin_forwarding(
        self, 
        from_: nextcord.abc.Snowflake, 
        to: nextcord.abc.Snowflake, 
        message: nextcord.Message
    ) -> None:
        from_ = await self.bot.fetch_channel(from_)
        to = await self.bot.fetch_channel(to)


        # Check if the "from_" channel exists in the database
        db_channel = self.db.query(database.Channel).filter_by(id=from_.id).first()

        if not db_channel:
            # If it doesn't exist, create a new record in the database
            db_channel = database.Channel(id=from_.id, forwarded_to=to.id, last_forward_message_id=message.id)
            self.db.add(db_channel)
            self.db.commit()

        # Check if the channel is paused in the database
        if db_channel.paused:
            await from_.send(f"Forwarding paused to {to.name}.")
            await to.send(f"Forwarding paused from {from_.name}.")
            return

        # Get the message history of the "from_" channel
        messages = await from_.history(limit=25, after=message, oldest_first=True).flatten()
        if len(messages) == 0:
            await from_.send(f"Done forwarding all messages from {to.name}.")
            await to.send(f"Done forwarding all messages from {from_.name}.")
            self.stop_forward(from_.id)
            return

        for message in messages:
            # Forward the message to the "to" channel
            await self.forward(to, message)

            # Update the last_forward_message_id in the database
            db_channel.last_forward_message_id = message.id
            self.db.commit()

        # Recursively call this method to forward the next chunk of messages
        last_message = await from_.fetch_message(db_channel.last_forward_message_id)
        await self.begin_forwarding(from_.id, to.id, last_message)

    async def forward(
        self,
        channel: nextcord.TextChannel,
        message: nextcord.Message,
    ) -> None:
        # Get the author's name and the message date
        author = message.author.display_name
        date = message.created_at.strftime("%Y-%m-%d %H:%M:%S")

        # Format the message content
        content = f"**{author}** *({date})*:\n{message.content}"

        # Get the message files and embeds
        files = [await attachment.to_file() for attachment in message.attachments] if message.attachments else None
        embeds = message.embeds

        #TODO: Embeds that come from a url to a file don't render properly

        # Send a message with the content, files, and embeds
        await channel.send(
            content=content,
            files=files,
            embeds=embeds,
            mention_author=False,
        )

    @nextcord.slash_command(
        description="Resume forwarding to another channel.",
        default_member_permissions=nextcord.Permissions().VALID_FLAGS["administrator"],
    )
    async def resume_forwarding(
        self, 
        interaction: nextcord.Interaction,
        channel_id,
    ) -> None:
        channel = await self.bot.fetch_channel(channel_id)
        

        # Check if the "from_" channel exists in the database
        db_channel = self.db.query(database.Channel).filter_by(id=channel_id).first()

        if db_channel:
            # Start forwarding from the last forwarded message in the channel
            message = await channel.fetch_message(db_channel.last_forward_message_id)
            await self.begin_forwarding(db_channel.id, db_channel.forwarded_to, message)

            # Set the "paused" flag to False and commit the changes to the database
            db_channel.paused = False
            self.db.commit()
            
            await interaction.response.send_message(f"Forward session resumed for channel {channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No forward session found for channel {channel.mention}.", ephemeral=True)

    @nextcord.slash_command(
        description="Forward messages to another channel.",
        default_member_permissions=nextcord.Permissions().VALID_FLAGS["administrator"],
    )
    async def forwarder(self, 
        interaction: nextcord.Interaction, 
        from_: nextcord.TextChannel, 
        to,
        after_message: int = None,
    ) -> None:
        if not after_message:
            after_message = (await interaction.channel.history(limit=1, oldest_first=True).flatten())[0]
        else:
            after_message = await interaction.channel.fetch_message(after_message)

        await self.begin_forwarding(from_.id, to, after_message)

    @nextcord.slash_command(
        description="Pause forwarding to another channel.",
        default_member_permissions=nextcord.Permissions().VALID_FLAGS["administrator"],
    )
    async def pause(
        self, 
        interaction: nextcord.Interaction,
        channel_id,
    ):
        channel = await self.bot.fetch_channel(channel_id)

        # Check if the channel exists in the database
        db_channel = self.db.query(database.Channel).filter_by(id=channel.id).first()

        if db_channel:
            # Pause the channel
            db_channel.paused = True
            self.db.commit()

            await interaction.response.send_message(f"Forward session paused for channel {channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No forward session found for channel {channel.mention}.", ephemeral=True)

    def stop_forward(self, channel_id):
        # Check if the channel exists in the database
        db_channel = self.db.query(database.Channel).filter_by(id=channel_id).first()

        if db_channel:
            # Delete the channel from the database
            self.db.delete(db_channel)
            self.db.commit()

    @nextcord.slash_command(
        description="End a forward session.",
        default_member_permissions=nextcord.Permissions().VALID_FLAGS["administrator"],
    )
    async def end(self, interaction: nextcord.Interaction, channel_id):
        self.stop_forward(channel_id)


    @nextcord.slash_command(
        description="List all current forwards.",
        default_member_permissions=nextcord.Permissions().VALID_FLAGS["administrator"],
    )
    async def forwards(self, interaction: nextcord.Interaction):
        forwards = self.db.query(database.Channel).all()

        if not forwards:
            await interaction.response.send_message("No forwards found.", ephemeral=True)
        else:
            forward_lines = []

            for forward in forwards:
                from_channel = self.bot.get_channel(forward.id)
                to_channel = self.bot.get_channel(forward.forwarded_to)

                if not from_channel or not to_channel:
                    continue

                status = "PAUSED" if forward.paused else "ACTIVE"


                forward_lines.append(f"{from_channel.name}:{from_channel.id} -> {to_channel.name}:{to_channel.id} ({status})")

            if not forward_lines:
                await interaction.response.send_message("No forwards found.", ephemeral=True)
            else:
                await interaction.response.send_message("```\n" + "\n".join(forward_lines) + "```")




def setup(bot):
    bot.add_cog(Forwarder(bot))
