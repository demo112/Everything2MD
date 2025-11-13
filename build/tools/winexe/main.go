package main

import (
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
)

func main() {
    exePath, err := os.Executable()
    if err != nil {
        fmt.Println("init error")
        os.Exit(1)
    }
    baseDir := filepath.Dir(exePath)
    depsDir := filepath.Join(baseDir, "deps")
    srcDir := filepath.Join(baseDir, "src")

    busybox := filepath.Join(depsDir, "busybox.exe")
    if _, err := os.Stat(busybox); err != nil {
        fmt.Println("missing busybox")
        os.Exit(1)
    }

    if _, err := os.Stat(srcDir); err != nil {
        fmt.Println("missing src")
        os.Exit(1)
    }

    lo1 := filepath.Join(baseDir, "LibreOfficePortable", "App", "libreoffice", "program")
    lo2 := filepath.Join(os.Getenv("ProgramFiles"), "LibreOffice", "program")
    lo3 := filepath.Join(os.Getenv("ProgramFiles(x86)"), "LibreOffice", "program")

    pathEnv := os.Getenv("PATH")
    addPaths := []string{depsDir, filepath.Join(depsDir, "python")}
    if stat, err := os.Stat(filepath.Join(lo1, "soffice.exe")); err == nil && !stat.IsDir() {
        addPaths = append(addPaths, lo1)
    }
    if stat, err := os.Stat(filepath.Join(lo2, "soffice.exe")); err == nil && !stat.IsDir() {
        addPaths = append(addPaths, lo2)
    }
    if stat, err := os.Stat(filepath.Join(lo3, "soffice.exe")); err == nil && !stat.IsDir() {
        addPaths = append(addPaths, lo3)
    }

    for _, p := range addPaths {
        if pathEnv == "" {
            pathEnv = p
        } else {
            pathEnv = p + ";" + pathEnv
        }
    }

    args := []string{"sh", filepath.Join(srcDir, "main.sh")}
    if len(os.Args) > 1 {
        args = append(args, os.Args[1:]...)
    }

    cmd := exec.Command(busybox, args...)
    cmd.Env = append(os.Environ(), "PATH="+pathEnv)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    cmd.Stdin = os.Stdin
    if err := cmd.Run(); err != nil {
        if exitErr, ok := err.(*exec.ExitError); ok {
            os.Exit(exitErr.ExitCode())
        }
        os.Exit(1)
    }
}
