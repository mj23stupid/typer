class Typer < Formula
  include Language::Python::Virtualenv

  desc "Typing practice in your terminal — like monkeytype for the CLI"
  homepage "https://github.com/willgerstung/typecli"
  url "https://github.com/willgerstung/typecli/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "UPDATE_THIS_AFTER_RELEASE"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "typer", shell_output("#{bin}/typer --help")
  end
end
