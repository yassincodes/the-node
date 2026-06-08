on run
  set mePath to POSIX path of (path to me)
  set bundled to mePath & "Contents/Resources/The Node.app"
  set installDir to (POSIX path of (path to home folder)) & "Applications/The Node"
  set dest to installDir & "/The Node.app"

  try
    display dialog "Install The Node on this Mac?" & return & return & "Everything stays on this computer. Encrypted." buttons {"Cancel", "Install"} default button "Install" with title "The Node"

    do shell script "mkdir -p " & quoted form of installDir
    do shell script "rm -rf " & quoted form of dest
    do shell script "ditto " & quoted form of bundled & " " & quoted form of dest
    do shell script "xattr -dr com.apple.quarantine " & quoted form of dest & " 2>/dev/null; xattr -cr " & quoted form of dest & " 2>/dev/null; true"
    do shell script "open " & quoted form of dest

    display dialog "Done." & return & return & "The Node is in Applications." buttons {"OK"} default button "OK" with title "The Node"
  on error errMsg
    display dialog errMsg buttons {"OK"} default button "OK" with title "The Node" with icon stop
  end try
end run
