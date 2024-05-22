#!/usr/bin/env bash

set -euo pipefail

current_script_path=${BASH_SOURCE[0]}
plugin_dir=$(dirname "$(dirname "$current_script_path")")

TOOL_NAME="ansible"
TOOL_TEST="ansible --version"

fail() {
	echo -e "asdf-$TOOL_NAME: $*"
	exit 1
}

sort_versions() {
	sed 'h; s/[+-]/./g; s/.p\([[:digit:]]\)/.z\1/; s/$/.z/; G; s/\n/ /' |
		LC_ALL=C sort -t. -k 1,1 -k 2,2n -k 3,3n -k 4,4n -k 5,5n | awk '{print $2}'
}

list_all_versions() {
	python3 "${plugin_dir}/lib/list-all-verisons.py"
}

install_version() {
	local install_type="$1"
	local version="$2"
	local install_path="$3"

	if [ "$install_type" != "version" ]; then
		fail "asdf-$TOOL_NAME supports release installs only"
	fi

	(
		python3 "${plugin_dir}/lib/check-python-version.py"
	) || (
		fail "Python version requires >= 3.5"
	)

	(
		venv_path="$install_path/venv"
		python3 -m venv "$venv_path"

		"$venv_path/bin/python3" -m pip install packaging >/dev/null 2>&1
		if ! "$venv_path/bin/python3" "${plugin_dir}/lib/check-package-version.py" "$version"; then
			exit 1
		fi
		"$venv_path/bin/pythin3" -m pip uninstall packaging >/dev/null 2>&1

		temp_path="$install_path/tmp"
		mkdir -p "$temp_path"
		temp_file="$temp_path/initial_files.txt"
		ls "$venv_path/bin" >"$temp_file"

		if ! "$venv_path/bin/python3" -m pip install ansible=="$version"; then
			exit 1
		fi

		mkdir -p "$install_path/bin"
		current_files=$(ls "$venv_path/bin")
		for file in $current_files; do
			if ! grep -q "$file" "$temp_file"; then
				ln -sf "$venv_path/bin/$file" "$install_path/bin/$file"
			fi
		done

		rm -rf "$temp_path"

		local tool_cmd
		tool_cmd="$(echo "$TOOL_TEST" | cut -d' ' -f1)"
		test -x "$install_path/bin/$tool_cmd" || fail "Expected $install_path/bin/$tool_cmd to be executable."

		echo "$TOOL_NAME $version installation was successful!"
	) || (
		rm -rf "$install_path"
		fail "An error occurred while installing $TOOL_NAME $version."
	)
}
