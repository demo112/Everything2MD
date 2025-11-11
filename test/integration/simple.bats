#!/usr/bin/env bats

@test "should show bats version" {
    run /Users/cooperd/UNV/TraeProject/Everything2MD/test/bats/bin/bats -v
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Bats" ]]
}