from monolith.background import *
from monolith.app import create_app
class TestBackgroundTasks:
    
    def test_get_new_app(self):
        app = do_task()
        assert app is not None
    
  
