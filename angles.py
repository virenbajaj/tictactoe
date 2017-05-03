import math,numpy

def simplify(ang):
  """simplifies a radian angle to be between (-pi and pi]"""
  if type(ang)==list:
    for i in range(len(ang)):
      ang[i] = simplify(ang[i])
    return ang
  else:
    ang = ang % (2*math.pi)
    if ang > math.pi: return ang-2*math.pi
    else:             return ang

def homog(pt):
  """converts 3D tuple to 4D numpy homogeneous point"""
  (x,y,z) = pt
  return numpy.matrix([[x],[y],[z],[1]])

def dehomog(pt):
  """converts 4D numpy homogeneous point back to 3D tuple"""
  point = pt.tolist()
  x = point[0][0]
  y = point[1][0]
  z = point[2][0]
  w = point[3][0]
  return (x/w,y/w,z/w)

def invMat(mat):
  """gets the inverse of a matrix"""
  return numpy.linalg.inv(mat)

def translation(x=0,y=0,z=0,trans=None):
  """Returns a 4x4 translation matrix"""
  try: #parse a numpy mat
    if trans.shape == (1,4) or trans.shape == (4,1):
      print("THIS IS AN ERROR")
      return -1
    if trans.shape == (1,3):
      (x,y,z) = trans.tolist()[0]
    else:
      assert(trans.shape == (3,1))
      (x,y,z) = trans.transpose().tolist()[0]
  except:
    try:
      (x,y,z) = trans
    except:
      pass #assume x,y,z are correct
  return numpy.matrix([[1,0,0,x],[0,1,0,y],[0,0,1,z],[0,0,0,1]])

def rotation(xang=0,yang=0,zang=0,rot=None):
  """Returns a 4x4 rotation (about the origin) matrix"""
  if rot is not None:
    try: #parse a numpy mat
      if rot.shape == (1,3):
        (xang,yang,zang) = rot.tolist()[0]
      else:
        assert(rot.shape == (3,1))
        (xang,yang,zang) = rot.transpose().tolist()[0]
    except:
      try:
        (xang,yang,zang) = rot
      except:
        pass #assume xang,yang,zang are correct

  xcos = math.cos(xang)
  xsin = math.sin(xang)
  ycos = math.cos(yang)
  ysin = math.sin(yang)
  zcos = math.cos(zang)
  zsin = math.sin(zang)

  xmat=numpy.matrix([[    1,    0,    0,0],\
                     [    0, xcos, xsin,0],\
                     [    0,-xsin, xcos,0],\
                     [    0,    0,    0,1]])

  ymat=numpy.matrix([[ ycos,    0,-ysin,0],\
                     [    0,    1,    0,0],\
                     [ ysin,    0, ycos,0],\
                     [    0,    0,    0,1]])

  zmat=numpy.matrix([[ zcos, zsin,    0,0],\
                     [-zsin, zcos,    0,0],\
                     [    0,    0,    1,0],\
                     [    0,    0,    0,1]])
  return zmat*ymat*xmat

def quat2rot(quat):
    q0,q1,q2,q3 = quat
    #from touretzky transform.py
    q0_sq = q0*q0; q1_sq = q1*q1; q2_sq = q2*q2; q3_sq = q3*q3
    t_q0q1 = 2. * q0 * q1
    t_q0q2 = 2. * q0 * q2
    t_q0q3 = 2. * q0 * q3
    t_q1q2 = 2. * q1 * q2
    t_q1q3 = 2. * q1 * q3
    t_q2q3 = 2. * q2 * q3
    return numpy.array([
        [ q0_sq+q1_sq-q2_sq-q3_sq, t_q1q2-t_q0q3,           t_q1q3+t_q0q2,           0. ],
        [ t_q1q2+t_q0q3,           q0_sq-q1_sq+q2_sq-q3_sq, t_q2q3-t_q0q1,           0. ],
        [ t_q1q3-t_q0q2,           t_q2q3+t_q0q1,           q0_sq-q1_sq-q2_sq+q3_sq, 0. ],
        [             0.,                     0.,                      0.,           1.  ]])

def extractRot(listmat):
  #don't question it I did the math this is right
  if(type(listmat) != list): listmat = listmat.tolist()

  ysin = listmat[2][0]
  yang = math.asin(ysin)

  ycosxcos = listmat[2][2]
  xcos = ycosxcos/math.cos(yang)
  xang = math.acos(xcos)

  zcosycos = listmat[0][0]
  zcos = zcosycos / math.cos(yang)
  zang = math.acos(zcos)

  return [xang,yang,zang]

def rotEq(rotmat1,rotmat2,err=0.05):
  if type(rotmat1) in [list,tuple]: rotmat1 = rotation(rot=rotmat1)
  if type(rotmat2) in [list,tuple]: rotmat2 = rotation(rot=rotmat2)

  pt = homog([1,0,0])
  pt1 = dehomog(rotmat1*pt)
  pt2 = dehomog(rotmat2*pt)
  dist = ((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2+(pt1[2]-pt2[2])**2)**0.5
  return dist <= err

def transform(pt,mat):
  return dehomog(mat*homog(pt))
