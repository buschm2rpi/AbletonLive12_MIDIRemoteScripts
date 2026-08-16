#!zsh

export dir=$1
export destination='/Users/michael/Music/Ableton/User Library/Remote Scripts'

rm -r "$destination"/"$dir"

cp -r "$dir" "$destination"/