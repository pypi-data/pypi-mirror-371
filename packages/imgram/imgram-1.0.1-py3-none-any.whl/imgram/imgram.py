from instagrapi import Client
import instagrapi
import click
from pathlib import Path
import json
import pwinput

@click.command()
@click.argument("url")
@click.option("-o", "--output", default="./", help="The path to the folder where you want to download to")
def imgram(url, output):
    client = Client()
    with open(Path(__file__).parent / "login.json", "r+") as f:
        login = json.load(f)
        if login["username"] == "" or login["password"] == "":
            login["username"] = input("Username: ")
            login["password"] = pwinput.pwinput()
            f.seek(0)
            json.dump(login, f, indent=4)
        
        loggedIn = False
        while not loggedIn:
            try:
                click.echo("Trying to log in…")
                if client.login(login["username"], login["password"]):
                    click.echo("Logged in succesfully!")
                    loggedIn = True
            except instagrapi.exceptions.UnknownError as error:
                if str(error).startswith("We can't find an account with"):
                    click.echo("Username is incorrect, please enter again")
                    with open(Path(__file__).parent / "login.json", "w") as f:
                        login["username"] = input("Username: ")
                        json.dump(login, f, indent=4)
            except instagrapi.exceptions.BadPassword:
                click.echo("Password is incorrect, please enter again")
                with open(Path(__file__).parent / "login.json", "w") as f:
                    login["password"] = pwinput.pwinput()
                    json.dump(login, f, indent=4)

    click.echo("Retrieving post data…")
    mediaPk = client.media_pk_from_url(url)
    click.echo("Retrieving post type…")
    try:
        mediaType = client.media_info(mediaPk).media_type
    except instagrapi.exceptions.InvalidMediaId:
        click.echo("Link was invalid")
        return
    productType = client.media_info(mediaPk).product_type

    isDownloading = False
    finished = False

    while not finished:
        try:
            if mediaType == 1:
                isDownloading = True
                click.echo("Downloading photo…")
                client.photo_download(mediaPk, output)
            elif mediaType == 2:
                if productType == "feed":
                    isDownloading = True
                    click.echo("Downloading video…")
                    client.video_download(mediaPk, output)
                elif productType == "igtv":
                    isDownloading = True
                    click.echo("Downloading igtv…")
                    client.igtv_download(mediaPk, output)
                elif productType == "clips":
                    isDownloading = True
                    click.echo("Downloading reel…")
                    client.clip_download(mediaPk, output)
            elif mediaType == 8:
                isDownloading = True
                click.echo("Downloading album…")
                client.album_download(mediaPk, output)
            finished = True
        except TimeoutError:
            click.echo("Timed out, trying again…")

    if isDownloading:
        click.echo("Finished downloading!")
    else:
        click.echo("Oh oh, something went wrong")