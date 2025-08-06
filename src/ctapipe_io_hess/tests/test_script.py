def test_fib(capsys, monkeypatch):
    from ctapipe_io_hess.cli.fib import main

    monkeypatch.setattr("sys.argv", ["fib", "10"])
    main()

    captured = capsys.readouterr()
    assert captured.out == "55\n"
