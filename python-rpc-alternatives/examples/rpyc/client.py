import rpyc

if __name__ == "__main__":
    conn = rpyc.connect("localhost", 18861)
    print("2 + 5 =", conn.root.add(2, 5))
    conn.close()
