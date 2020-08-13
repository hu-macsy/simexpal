
import selectors
import weakref

READ = selectors.EVENT_READ
WRITE = selectors.EVENT_WRITE

class Descriptor:
	def __init__(self, loop, fn, fd=None):
		self._loop_ref = weakref.ref(loop)
		self.fn = fn
		self.fd = fd

		self.has_run = False
		self.mask = None

	def get_loop(self):
		loop = self._loop_ref()
		assert loop
		return loop

class Handle:
	def __init__(self, loop, desc, do_unregister):
		self._desc_ref = weakref.ref(desc)
		self._do_unregister = do_unregister
		self._was_unregistered = False

	def unregister(self):
		if self._was_unregistered:
			return

		desc = self._desc_ref()
		assert desc
		self._do_unregister(desc.get_loop(), desc)
		self._was_unregistered = True

class EventLoop:
	@staticmethod
	def _unregister_observer(self, desc):
		self._observers.remove(desc)
		self._refcount -= 1

	@staticmethod
	def _unregister_file(self, desc):
		self._sel.unregister(desc.fd)
		self._refcount -= 1

	@staticmethod
	def _unregister_idle(self, desc):
		self._idle.remove(desc)
		self._refcount -= 1

	def __init__(self):
		self._active = True
		self._refcount = 0
		self._sel = selectors.DefaultSelector()

		self._observers = set()
		self._idle = set()

	def shutdown(self):
		print("Shutting down event loop")
		assert self._active
		self._active = False

	def register_observer(self, fn):
		desc = Descriptor(self, fn)
		self._observers.add(desc)
		self._refcount += 1
		return Handle(self, desc, EventLoop._unregister_observer)

	def register_file(self, fd, mask, fn):
		desc = Descriptor(self, fn, fd=fd)
		self._sel.register(fd, mask, desc)
		self._refcount += 1
		return Handle(self, desc, EventLoop._unregister_file)

	def register_idle(self, fn):
		desc = Descriptor(self, fn)
		self._idle.add(desc)
		self._refcount += 1
		return Handle(self, desc, EventLoop._unregister_idle)

	def run(self):
		assert self._active
		assert self._refcount

		while self._refcount:
			# List of pending descriptors.
			pd = []

			# Schedule all observers that did not run yet.
			if not self._active:
				for desc in self._observers:
					if desc.has_run:
						continue
					pd.append(desc)

			# Schedule all I/O events.
			timeout = None
			# Do not block if there are any pending descriptors.
			if pd:
				timeout = 0
			events = self._sel.select(timeout)
			for key, mask in events:
				desc = key.data
				desc.mask = mask
				pd.append(desc)

			# Schedule all idle callbacks.
			pd = list(self._idle) + pd

			# Finally, run all events.
			for desc in pd:
				desc.fn(desc)
				desc.has_run = True

