#!/usr/bin/env bats

setup() {
    PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    BATS_BIN="$PROJECT_ROOT/test/bats/bin/bats"
}

@test "should show bats version" {
    run "$BATS_BIN" -v
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Bats" ]]
}