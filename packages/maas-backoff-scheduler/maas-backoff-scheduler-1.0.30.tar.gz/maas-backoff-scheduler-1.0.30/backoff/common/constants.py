# _*_ coding: utf-8 _*_
class Constants:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("can't change const %s" % name)
        if not name.isupper():
            raise self.ConstCaseError('const name "%s" is not all uppercase' % name)
        self.__dict__[name] = value


constants = Constants()
constants.FACE_SWAP_PROCESS_PROGRESS_FILE_NAME = "progress_{}_{}.txt"
constants.MYSQL_TABLE_USER_NAME = "meta_user"
