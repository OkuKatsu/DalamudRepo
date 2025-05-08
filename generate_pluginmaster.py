import json
import os
from os.path import getmtime
from zipfile import ZipFile

BRANCH = os.environ["GITHUB_REF"].split("refs/heads/")[-1]
DOWNLOAD_URL = "https://github.com/OkuKatsu/DalamudRepo/raw/{branch}/Plugins/{plugin_name}/latest.zip"
TESTING_DOWNLOAD_URL = "https://github.com/OkuKatsu/DalamudRepo/raw/{branch}/Plugins/{plugin_name}/testing/latest.zip"
GLOBAL_DOWNLOAD_URL = "https://github.com/OkuKatsu/DalamudRepo/raw/{branch}/Plugins/{plugin_name}/global/latest.zip"

DUPLICATES = {
    "DownloadLinkInstall": ["DownloadLinkUpdate"],
}

TRIMMED_KEYS = [
    "Author",
    "Name",
    "Punchline",
    "Description",
    "Tags",
    "InternalName",
    "RepoUrl",
    "Changelog",
    "AssemblyVersion",
    "ApplicableVersion",
    "DalamudApiLevel",
    "TestingAssemblyVersion",
    "TestingDalamudApiLevel",
    "IconUrl",
    "ImageUrls",
]


def main():
    master = extract_manifests()
    master = [trim_manifest(manifest) for manifest in master]
    add_extra_fields(master)
    write_master(master)
    last_update()


def extract_manifests():
    manifests = []
    for dirpath, dirnames, filenames in os.walk("./Plugins"):
        if "latest.zip" not in filenames:
            continue

        plugin_name = dirpath.split("/")[-1]
        base_zip = f"{dirpath}/latest.zip"

        with ZipFile(base_zip) as z:
            base_manifest = json.loads(z.read(f"{plugin_name}.json").decode("utf-8"))
            manifests.append(base_manifest)
    return manifests


def add_extra_fields(manifests):
    for manifest in manifests:
        manifest["DownloadLinkInstall"] = DOWNLOAD_URL.format(
            branch=BRANCH, plugin_name=manifest["InternalName"]
        )

        for src, targets in DUPLICATES.items():
            for target in targets:
                if target not in manifest:
                    manifest[target] = manifest[src]

        if "TestingAssemblyVersion" in manifest and not is_global:
            manifest["DownloadLinkTesting"] = TESTING_DOWNLOAD_URL.format(
                branch=BRANCH, plugin_name=manifest["InternalName"]
            )

        manifest["DownloadCount"] = 0


def write_master(master):
    with open("pluginmaster.json", "w") as f:
        json.dump(master, f, indent=4)


def trim_manifest(plugin):
    return {k: plugin[k] for k in TRIMMED_KEYS if k in plugin}


def last_update():
    with open("pluginmaster.json", encoding="utf-8") as f:
        master = json.load(f)

    for plugin in master:
        file_path = f"Plugins/{plugin['InternalName']}/latest.zip"

        modified = int(getmtime(file_path))
        if "LastUpdate" not in plugin or modified != int(plugin.get("LastUpdate", 0)):
            plugin["LastUpdate"] = str(modified)

    with open("pluginmaster.json", "w", encoding="utf-8") as f:
        json.dump(master, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
