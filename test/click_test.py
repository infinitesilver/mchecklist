import click

@click.command()
@click.option('--path', help='path to destination')
def path_create(path: str):
    """Creates the designated path! (Not actually, just pretends to)"""
    print(f"{path} created.")

if __name__ == '__main__':
    path_create()