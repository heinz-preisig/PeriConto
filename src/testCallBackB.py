
from testCallBackA import A

class B:
  def __init__(self):
    self.me = "me"

    self.a = A(self)


  def remember(self, s):
    print("this is B", s)


if __name__ == "__main__":
  b = B()
  b.a.gugus("hello")
  b.a.corr("hello again")