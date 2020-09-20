function out = load_mat( matfile )

m = load(matfile);

% Python Matfiles come in with many additional layers of cell arrays
% This compacts them out
%
f = fieldnames(m)
for k = 1:numel(f)
  field = f(k)
  field = field{1}
  out.(field) = [m.(field){:}]
end

if isfield(out, 'MWC')
  for p = 1:numel(out.MWC)
    out.MWC(p).beamData = [out.MWC(p).beamData{:}];
  end
end
