# -*- coding: utf-8 -*-
# @Time    : 2025/1/15 10:25
# @Author  : hxq
# @File    : mdeol.py
import click


@click.command()
@click.option('--name', prompt='Your name', help='Your name')
def main(name):
    click.echo(f"Hello, {name}, this is my package running from cmd!")
