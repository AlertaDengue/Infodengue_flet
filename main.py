import flet as ft


async def main(page: ft.Page):
    page.title = "Infodengue"

app = ft.app(
    target=main,
    export_asgi_app=True,
    assets_dir="assets",
    # upload_dir="data"
)


def run():
    ft.app(
        target=main,
        assets_dir="assets",
        upload_dir="data"
    )


if __name__ == "__main__":
    pass
    run()
