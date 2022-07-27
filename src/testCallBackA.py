


class A:
  def __init__(self, B):
    self.B = B

  def gugus(self, s):
    print("this is A", s)

    self.B.remember("B calling")

  def corr(self, s):
    print("this is A corr", s)