__unreal_engine_path="/home/catec/UnrealEngine/" # TUNE ME


# Launches an instance of Unreal Engine Editor pointing to a particular project, 
# which may be provided as argument as either .uproject file or a path containing
# one. If ran with no arguments, runs a bare editor instance.
# 
# Usage: 
#     UE4Editor [{ file.uproject | MyProject/ }] --
# 
UE4Editor () {
    local target="$1"
    local target="$(readlink -f "$target")" 
    local editor="$__unreal_engine_path/Engine/Binaries/Linux/UE4Editor" 

    # If no argument, simply run the editor
    if [ -z "$1" ]; then
        $editor
    fi

	# Directory, try to find uprojects here
    if [[ -d $target ]]; then
		nresults=$(ls "$target"/*.uproject 2>/dev/null | wc -l)

		if [[ $nresults -eq 1 ]]; then
			$editor "$(ls "$target"/*.uproject)"

		elif [[ $nresults -gt 1 ]]; then 
			echo "Error: too many .uproject files, directory input not allowed."
			ls -1 "$target"/*.uproject 

		elif [[ $nresults -eq 0 ]]; then
			echo "Error: did not find any .uproject file."

		else
			echo "Error: unexpected error."
		fi

	# File, check extension and run
	elif [[ -f $target ]]; then

		if [[ "$target" == *.uproject ]]; then
			$editor "$target"
		else
			echo "Error: not an .uproject file."
		fi

	# Something else: bad news 
	else
		echo "$target is not valid"
	fi
}

# Launches a Linux mono recompilation with default arguments of an unreal project,
# which may be provided as argument as either .uproject file or a path containing
# one. 
# 
# Usage: 
#     UE4Magic { file.uproject | MyProject/ } --
# 
UE4Magic () {
    local target="$1"
    local target="$(readlink -f "$target")"
    local uepath="$__unreal_engine_path"

    # If no argument, crash 
    if [ -z "$1" ]; then
        echo "Error: no arguments provided."
    fi

	# Directory, try to find uprojects here
    if [[ -d $target ]]; then
		nresults=$(ls "$target"/*.uproject 2>/dev/null | wc -l)

		if [[ $nresults -eq 1 ]]; then
			pushd "$uepath"
			./Engine/Binaries/ThirdParty/Mono/Linux/bin/mono ./Engine/Binaries/DotNET/UnrealBuildTool.exe Development Linux -Project="$(ls "$target"/*.uproject)" -TargetType=Editor -Progress
			popd
		elif [[ $nresults -gt 1 ]]; then 
			echo "Error: too many .uproject files, directory input not allowed."
			ls -1 "$target"/*.uproject 

		elif [[ $nresults -eq 0 ]]; then
			echo "Error: did not find any .uproject file."
            
		else
			echo "Error: unexpected error."
		fi

	# File, check extension and run
	elif [[ -f $target ]]; then

		if [[ "$target" == *.uproject ]]; then
			pushd "$uepath"
			./Engine/Binaries/ThirdParty/Mono/Linux/bin/mono ./Engine/Binaries/DotNET/UnrealBuildTool.exe Development Linux -Project="$(ls "$target"/*.uproject)" -TargetType=Editor -Progress
			popd
		else
			echo "Error: not an .uproject file."
		fi

	# Something else: bad news 
	else
		echo "$target is not valid"
	fi

}
