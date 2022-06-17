from graph import Matrix

def main():
    connections = [
        ("a", "b"),
        ("b", "c"),
        ("f", "y"),
    ]
    m = Matrix(connections, is_bidirectional=True)
    print(m.are_connected_bfs("c", "a"))


if __name__ == "__main__":
    main()
